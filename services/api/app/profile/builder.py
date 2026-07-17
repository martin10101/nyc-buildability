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

Task M2-T004 (owner code-audit P1, 2026-07-17) additions:

- ``status_dimensions``: five INDEPENDENT dimensions (source-record
  completeness, analysis readiness, rule coverage, geometry validity,
  financial readiness), never collapsed into one label (PRD s12; GDS s3.3).
  Dimensions the platform cannot yet compute are declared ``not_computed`` -
  never inferred, never invented.
- Overall completeness (``data_completeness`` and the new
  ``source_record_completeness``) is derived ONLY from the documented
  FEASIBILITY_COLUMNS basis below - never again from all 108 possible PLUTO
  columns (the pre-M2-T004 defect that made ``complete`` unreachable).
- ``reproducibility`` gains ``response_digest`` + ``digest_canonicalization``
  (canonical snapshot digest of the exact response the profile was built
  from, plus the verbatim canonicalization spec used to compute it).
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from app.connectors.pluto_soda import (
    CANONICALIZATION_SPEC,
    DATASET_ID,
    SOURCE_ID,
    PlutoFetchResult,
)

__all__ = [
    "CRITICAL_COLUMNS",
    "FEASIBILITY_COLUMNS",
    "GEOMETRY_COLUMNS",
    "PROFILE_CONTRACT_VERSION",
    "build_property_profile",
]

# CONTRACT VERSION DECLARED BY THIS BUILDER (task M2-T003 established the
# declare-what-you-emit rule; task M2-T006 advances it to 1.3.0).
#
# The builder emits keys through 1.3.0 (the M2-T004 set plus the typed
# reproducibility.staleness object, which it emits on EVERY serve), so it
# DECLARES 1.3.0 - the canonical contract version whose key set it fully
# covers. Because every added key is optional, previously accepted 1.0.0,
# 1.1.0, and 1.2.0 instances remain valid and are served unchanged (backward
# compatibility); the value is validated against the closed published enum by
# app.profile.contract (including the declared-vs-emitted consistency check
# on the dotted path "reproducibility.staleness"), never hard-coded against a
# stale version.
PROFILE_CONTRACT_VERSION = "1.3.0"

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

# ---------------------------------------------------------------------------
# FEASIBILITY-RELEVANT COMPLETENESS BASIS (task M2-T004, owner P1 bullet 1).
#
# THE defect fix: data_completeness / source_record_completeness are derived
# ONLY from this documented 19-column basis, never again from all 108 possible
# PLUTO columns (which made "complete" unreachable because SODA omits null
# fields per record and most lots legitimately lack columns like zonedist4).
#
# This is a PLATFORM completeness policy, not a legal interpretation. Every
# column below exists in the official 108-column SODA inventory (fixture
# F08_api_views_columns_snapshot.json, /api/views/64uk-42ks.json, retrieved
# 2026-07-16) and its meaning is grounded in the official "PLUTO DATA
# DICTIONARY - May 2026 (26v1)" (https://s-media.nyc.gov/agencies/dcp/assets/
# files/pdf/data-tools/bytes/pluto_datadictionary.pdf, G1-verified direct
# read) as documented in docs/research/pluto-mappluto-2026-07-16.md
# (dictionary page numbers below cite that research doc's section 4.1/4.3).
#
# CRITICAL columns - prerequisites for ANY feasibility calculation:
#   lotarea    dict p.21: "Total area of the tax lot, expressed in square
#              feet" - the multiplicand of every floor-area computation.
#   zonedist1  primary zoning district assignment (README 26v1 minor-release
#              zoning attribute, research s3.2; the FAR reference columns are
#              "based on ZoneDist1", dict p.36-37) - rule applicability basis.
#
# NONCRITICAL feasibility-relevant columns:
#   lot geometry/configuration: lotfront, lotdepth (dict p.29, feet),
#     lottype, irrlotcode (lot-configuration codes in the official inventory;
#     code-list appendix meanings = research OQ-5 residual - membership here
#     requires only presence, no code interpretation), splitzone (README
#     minor-release zoning attribute; split-lot detection is PRD s3 required).
#   existing use: landuse, bldgclass (official classification codes,
#     inventory F08; appendices B-D per research s4.1).
#   existing building: bldgarea (dict p.22, sq ft, condo caveat), numbldgs,
#     numfloors (dict p.28 incl. the null+NumBldgs>0 "not available" rule),
#     unitsres, unitstotal (E2 verbatim field list), yearbuilt (dict p.34-35:
#     null/0 = unknown), builtfar.
#   FAR reference (informational, never rule outputs - research s4.1):
#     residfar, commfar, facilfar (dict p.36-37, exclusive of bonuses).
#
# DOCUMENTED EXCLUSIONS (absence NEVER degrades completeness):
#   1. Conditional-presence zoning/regulatory columns (zonedist2-4,
#      overlay1-2, spdist1-3, ltdheight, landmark, histdist, edesignum,
#      zonemap, zmcode, transitzone, mih_opt1-4, firm07_flag, pfirm15_flag,
#      appbbl, appdate, condono, ext, easements, dcpedited, notes, vintage
#      dates, and the 26v1-new affordable/manufacturing FAR reference columns
#      affresfar and mnffar): under SODA null-omission (research s2.1/s4.2
#      critical caveat) their absence is not distinguishable from "none/not
#      applicable", and the verified research does not define per-column null
#      semantics for them - counting them recreates the 108-column defect.
#      affresfar/mnffar are additionally, like residfar/commfar/facilfar,
#      informational reference values that must never become rule outputs;
#      unlike those three they are new in 26v1 with conditional presence
#      (program-dependent), so they stay out of the basis (G1 correction C2).
#      When PRESENT they surface as facts/mapped features with full provenance.
#   2. Geometry columns (GEOMETRY_COLUMNS below): owned by the INDEPENDENT
#      geometry_validity dimension - never mixed into record completeness.
#   3. Identity/administrative columns (borough, block, lot, borocode, bbl,
#      address, zipcode, cd, ct2010, cb2010, bct2020, bctcb2020, tract2010,
#      schooldist, council, firecomp, policeprct, healtharea, sanit*,
#      healthcenterdistrict, ownername, ownertype, areasource, proxcode,
#      bsmtcode, bldgfront, bldgdepth, yearalter1-2, assessland, assesstot,
#      exempttot, use-area breakdowns, sanborn, taxmap, plutomapid, version):
#      identity integrity is enforced by the connector's exact-match +
#      consistency checks (conflicts feed analysis_readiness), and the rest
#      are administrative/valuation context, not feasibility inputs.
#
# KNOWN LIMITATION (disclosed, not hidden): zero-vs-null serving is
# officially verified only for numfloors (README: null shown for zero) and
# yearbuilt (dict p.34-35: null/0 = unknown). A genuinely vacant lot may
# therefore show 'partial' / missing_noncritical building columns until the
# M2 confirmation workflow or further verified research refines the policy;
# completeness never blocks analysis (only CRITICAL gaps gate readiness).
# ---------------------------------------------------------------------------

CRITICAL_COLUMNS: frozenset[str] = frozenset({"lotarea", "zonedist1"})

FEASIBILITY_COLUMNS: frozenset[str] = CRITICAL_COLUMNS | frozenset({
    "lotfront", "lotdepth", "lottype", "irrlotcode", "splitzone",
    "landuse", "bldgclass",
    "bldgarea", "numbldgs", "numfloors", "unitsres", "unitstotal",
    "yearbuilt", "builtfar",
    "residfar", "commfar", "facilfar",
})

# Geometry-bearing columns: excluded from the completeness basis BY DESIGN so
# source_record_completeness and geometry_validity stay independent (a record
# can be 'complete' while geometry is 'missing', and vice versa - GDS s3.3).
GEOMETRY_COLUMNS: frozenset[str] = frozenset({
    "latitude", "longitude", "xcoord", "ycoord", "geom",
})

# Identity fields whose unresolved conflicts block analysis readiness: a
# profile whose bbl/borocode/block/lot disagree cannot be trusted to describe
# ONE property (connector check_identifier_consistency fields + 'bbl').
_IDENTITY_CONFLICT_FIELDS: frozenset[str] = frozenset({
    "bbl", "borocode", "block", "lot",
})

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

# Verbatim per-profile policy for the five independent status dimensions
# (M2-T004): stored in every profile (status_dimensions.policy) so a
# historical report explains its own labels after the policy text evolves.
_STATUS_DIMENSIONS_POLICY = (
    "status_dimensions are derived deterministically and INDEPENDENTLY "
    "(owner code-audit P1 2026-07-17; PRD s12; GDS s3.3 - never collapsed "
    "into one label; dimensions not yet computable are declared "
    "'not_computed', never inferred). source_record_completeness: 'complete' "
    "when every column of the documented 19-column feasibility-relevant "
    "basis (builder FEASIBILITY_COLUMNS; official PLUTO 26v1 data "
    "dictionary, cited per column in the builder and "
    "docs/research/pluto-mappluto-2026-07-16.md) is present with a usable "
    "value, else 'partial'; a column is unusable when absent, officially "
    "unknown (numfloors null with buildings per dictionary p.28; yearbuilt "
    "0/null per p.34-35), or drift-flagged; absence of any other PLUTO "
    "column NEVER degrades this dimension (the 108-column denominator is "
    "retired). analysis_readiness, in order: 'blocked_data_conflict' when "
    "an unresolved conflict touches an identity field (bbl/borocode/block/"
    "lot) or a critical column; 'blocked_missing_critical' when a critical "
    "column (lotarea, zonedist1) is absent or drift-flagged; else 'ready' - "
    "a DATA statement only, NOT the PRD s32.1 workflow state, and never an "
    "assertion that user confirmation occurred. rule_coverage: "
    "'not_computed' until the M4 published-rule engine exists. "
    "geometry_validity: 'missing' when the source supplied no usable point "
    "geometry, else 'not_computed' until M2 tax-lot geometry validation "
    "lands. financial_readiness: 'not_computed' until a financial engine "
    "exists (GDS Phase C). data_completeness (legacy 3-value field) counts "
    "ONLY feasibility-relevant missing inputs: any critical -> "
    "missing_critical, any -> missing_noncritical, none -> complete."
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
    missing inputs - unknown is stated, never fabricated (PRD section 9).

    M2-T004: every entry carries ``feasibility_relevant`` (membership in the
    documented FEASIBILITY_COLUMNS completeness basis). ALL absent columns
    stay listed - visibility is unchanged - but ONLY feasibility-relevant
    entries drive data_completeness and source_record_completeness.
    """
    entries: dict[str, dict] = {}
    for column in result.absent_columns:
        entries[column] = {
            "field": column,
            "criticality": "critical" if column in CRITICAL_COLUMNS else "noncritical",
            "reason": (
                "column absent from the SODA record (null-omission semantics): "
                "the value is unknown for this tax lot and is never fabricated"
            ),
            "feasibility_relevant": column in FEASIBILITY_COLUMNS,
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
            "feasibility_relevant": field_name in FEASIBILITY_COLUMNS,
        }
    return [entries[key] for key in sorted(entries)]


def _status_dimensions(
    result: PlutoFetchResult,
    identity: dict,
    missing_inputs: list[dict],
    conflicts: list[dict],
    drift_columns: set[str],
) -> dict:
    """Five INDEPENDENT status dimensions (M2-T004; PRD s12; GDS s3.3).

    Deterministic code only. Each dimension is computed from its OWN inputs;
    none is inferred from another, and dimensions the platform cannot yet
    compute are declared 'not_computed' - never invented.
    """
    # Feasibility-basis columns that are unusable: absent or officially
    # unknown (missing_inputs covers both) or drift-flagged while present.
    unusable = {
        entry["field"] for entry in missing_inputs if entry["feasibility_relevant"]
    }
    unusable |= drift_columns & FEASIBILITY_COLUMNS
    source_record_completeness = "complete" if not unusable else "partial"

    # analysis_readiness - documented precedence order (see policy string):
    # identity/critical conflicts first (a profile that may describe two
    # different properties cannot be analyzed), then critical gaps.
    gating_conflict_fields = _IDENTITY_CONFLICT_FIELDS | CRITICAL_COLUMNS
    has_gating_conflict = any(
        conflict["field"] in gating_conflict_fields
        and conflict.get("resolution") == "unresolved"
        for conflict in conflicts
    )
    # CRITICAL_COLUMNS is a subset of FEASIBILITY_COLUMNS, so 'unusable'
    # already covers absent, officially-unknown, and drift-flagged criticals.
    critical_unusable = unusable & CRITICAL_COLUMNS
    if has_gating_conflict:
        analysis_readiness = "blocked_data_conflict"
    elif critical_unusable:
        analysis_readiness = "blocked_missing_critical"
    else:
        analysis_readiness = "ready"

    # geometry_validity: 'missing' is a POSITIVE statement that the source
    # supplied no usable geometry; a present (point) geometry is
    # 'not_computed' because the validation pipeline arrives with the M2
    # tax-lot geometry tasks - validity is unknown, not asserted.
    geometry_validity = "not_computed" if "geometry" in identity else "missing"

    return {
        "source_record_completeness": source_record_completeness,
        "analysis_readiness": analysis_readiness,
        # No published-rule engine exists before M4: applicability is not
        # computable, and anything but 'not_computed' would invent coverage.
        "rule_coverage": "not_computed",
        "geometry_validity": geometry_validity,
        # No financial engine exists before GDS Phase C.
        "financial_readiness": "not_computed",
        "policy": _STATUS_DIMENSIONS_POLICY,
    }


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
        additive keys ``data_completeness``, ``reproducibility``,
        ``status_dimensions`` (M2-T004), ``reproducibility.staleness``
        (M2-T006), and per-fact ``coverage_status`` are schema-permitted
        optional properties (same additive-extension pattern the accepted
        M1-T002 connector uses on source_fact); the required v1 field set is
        complete and unchanged, and the declared ``contract_version`` is
        ``1.3.0`` - the canonical version whose key set this builder fully
        covers (task M2-T003 established the rule; M2-T006 advanced the
        version). The API layer validates every built profile
        against the selected canonical schema before send
        (``app.profile.contract.validate_profile``), so an invalid 200 is
        impossible.
    """
    if result.status != "ok":
        raise ValueError(
            f"build_property_profile requires a status='ok' result, got "
            f"{result.status!r}; no_match/failure states are handled by the API layer"
        )
    if not result.response_digest:
        # Fail loudly rather than emit a profile whose snapshot lineage has a
        # gap (mirrors _assert_provenance_integrity: by construction the
        # accepted connector always sets it).
        raise ValueError(
            "build_property_profile requires result.response_digest; a profile "
            "must never lose the link to the exact response it was built from"
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
    # M2-T004 defect fix: the completeness denominator is the documented
    # FEASIBILITY_COLUMNS basis - entries outside it (feasibility_relevant
    # False) stay VISIBLE in missing_inputs but no longer drive the label.
    feasibility_missing = [e for e in missing_inputs if e["feasibility_relevant"]]
    if any(entry["criticality"] == "critical" for entry in feasibility_missing):
        data_completeness = "missing_critical"
    elif feasibility_missing:
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
            # M2-T004 snapshot lineage: the exact-response digest plus the
            # verbatim canonicalization spec needed to recompute/verify it.
            "response_digest": result.response_digest,
            "digest_canonicalization": CANONICALIZATION_SPEC,
            # M2-T006 contract 1.3.0: typed serve-freshness. The resilience
            # fetcher stamps result.staleness on cache-hit and last-known-good
            # serves (copied verbatim - never invented here); a fresh
            # retrieval carries None and truthfully becomes the fresh marker.
            # Emitted on EVERY serve (schema-documented pattern), so absence
            # can only mean a pre-1.3.0 producer.
            "staleness": dict(result.staleness)
            if result.staleness is not None
            else {"served_from_cache": False, "stale": False},
        },
    }
    profile["status_dimensions"] = _status_dimensions(
        result,
        profile["identity"],
        missing_inputs,
        profile["conflicts"],
        drift_columns,
    )
    _assert_provenance_integrity(profile)
    return profile
