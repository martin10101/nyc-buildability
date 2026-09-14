"""B4 - wide-street 100-ft buffer/intersection geometry engine (task
M4-T021, D-045 A2 geometry lane; pinned research ``project-control/reports/
M4-T016-a2-geometry-mechanics-research.md`` Part 2.2 steps A-D, Part 2.3
CRS/unit evidence, Part 2.4 edge cases EC-1..6, Part 4.3 item 2).

Computes ZR 23-22 footnote 1's "within 100 feet of a wide street" geometry
test: *"For zoning lots, or portions thereof, located within 100 feet of a
wide street."* (research Part 2.1, quoted verbatim, also pinned in
``r6_r7_r8_wide_street_conditional_far.rule.json``'s citations). This module
computes the geometry ONLY - it never re-classifies street width, never
decides the OQ-3 ambiguity-class policy, and never wires a rule file (B7 is
a later packet).

REUSE DISCIPLINE (contract item 1): both inputs are consumed by READ-ONLY
import from accepted connectors - the wide-disposed DCM segment polylines
from the accepted M4-T020 ``dcm_street_centerline_geometry`` (already
filtered by the CALLER to ``effective_disposition == 'wide'`` via the
accepted M4-T015 classifier / M4-T019 policy - never re-implemented or
re-decided here), and the MapPLUTO zoning-lot polygon measurement surface
from the accepted ``mappluto_geometry_arcgis.GeometryAssessment`` /
``canonical_to_shapely``. Neither accepted module is modified.

CRS FAIL-CLOSED, NO REPROJECTION (contract item 1; research Part 2.3): both
the DCM and MapPLUTO connectors already validate wkid 102718 / latestWkid
2263 (EPSG:2263, NAD83 New York Long Island, US survey foot -
"(ftUS)", confirmed independently at https://epsg.io/2263) before returning
any geometry - the same authoritative pair on both sides, so no reprojection
is required or performed. This module asserts that shared pin at import time
(rather than assuming it) and re-validates every caller-supplied CRS
identity independently before interpreting a single coordinate: absence or
mismatch on either the segment side or the lot side is the typed
``WrongCRSError``. There is NO reprojection call path anywhere in this
module (proven by the test suite's AST/token-scan, mirroring the accepted
M4-T020 precedent).

BUFFER (contract item 2): a planar buffer of exactly ``BUFFER_FT`` = 100.0
US survey feet per wide segment polyline, valid only because both CRSs are
the same projected, foot-unit CRS (never performed in unprojected degrees).
``shapely.__version__`` / ``shapely.geos_version_string`` are captured on
every result and cross-checked against the accepted
``mappluto_geometry_arcgis`` pins (``PINNED_SHAPELY_VERSION`` = "2.0.7" /
``PINNED_GEOS_VERSION_STRING`` = "3.11.4") for determinism, per the pyproject
discipline; the arc-approximation parameter (``BUFFER_QUAD_SEGS`` = 16) is
pinned explicitly for determinism, matching the real default of the
``BaseGeometry.buffer`` method actually called here (see the constant's own
comment for the verified distinction from the different, unused top-level
``shapely.buffer()`` function's default of 8).

INTERSECTION (contract item 3): both the boolean any-portion ``intersects``
test (ZR 23-22 footnote 1 "or portions thereof") and the actual intersection
sub-geometry/area are exposed - per segment (``SegmentContribution``) AND as
the union-before-intersect aggregate (``WideStreetBufferResult``), for the
rule layer's future apportionment.

EDGE CASES (contract item 4; research Part 2.4):
  EC-1 corner/multi-frontage lots are handled by union-by-construction - each
    qualifying segment contributes its own buffer, unioned via
    ``shapely.ops.unary_union`` BEFORE intersecting the lot (never summed).
  EC-2 ambiguous/narrow segments never reach this module (the caller's
    wide-only input contract); the resulting honest under-claim is
    documented on every result (``EC2_UNDER_CLAIM_NOTICE``) and in the
    producer report's tradeoff section - never silently absorbed.
  EC-3 every computation is per-segment (a segment corresponds to one
    ``AttestedWideSegment``/one DCM block-face record) - this module never
    assumes one width per named street.
  EC-4 exact-100-ft tangency gets NO silent tolerance: the GEOS
    ``intersects``/``intersection`` predicates run unmodified at the exact
    buffer boundary. ``mappluto_geometry_arcgis.BOUNDARY_TOLERANCE_FT`` (a
    POSITIONAL-ACCURACY constant for MapPLUTO's own +/-20-ft survey
    disclosure) is deliberately NEVER imported or referenced here - it is
    not a legal buffer allowance. The open tolerance question is documented
    (``TANGENCY_NOTICE``), not resolved.
  EC-5 the named-street override (Broadway W94-97 CD7; Allen St
    Rivington-Delancey CD3) and the C5-3/C6-4/C6-6 alternate-width clause
    are OUT of this module's scope (B7, later). The caller must supply a
    typed, no-default ``Ec5AttestedPreconditions`` (the accepted
    ``dcm_street_width_policy.AttestedPreconditions`` precedent), and - per
    the rework ruling in ``project-control/reports/M4-T021-rework-ruling.md``
    RULING 1 - this module now GATES computation on the attested values,
    mirroring that precedent's own mechanism exactly: when
    ``dcm_street_width_policy.AttestedPreconditions.exceptions_checked`` is
    ``False``, ``classify_street_width_policy`` refuses and returns
    ``DECISION_UNRESOLVED`` rather than a classification; analogously, when
    either ``named_street_override_checked`` or
    ``alternate_width_clause_checked`` is ``False``, this module refuses and
    returns the typed ``STATUS_PRECONDITIONS_NOT_ATTESTED`` result (every
    buffer/intersection field ``None``/empty, the reason visible in
    ``ec5_not_attested_notice``) instead of ``STATUS_COMPUTED`` - never a
    computed-looking number on unverified legal preconditions. Only an
    affirmative attestation (both fields ``True``) computes exactly as
    before. The attestation itself is always carried through on every
    result (including refusals) for audit.
  EC-6 an empty wide-segment input set returns the typed
    ``STATUS_NO_WIDE_SEGMENTS_PROVIDED`` result state - never a computed
    True or a computed False in either direction.

Zero new dependencies (shapely 2.0.7 is already admitted). No rule-file
edits. Deterministic code only: no AI, no legal interpretation, no rule
wiring, no lot-level zoning determination. All results are DRAFT-adjacent
geometry facts feeding a rule that itself remains DRAFT/needs-review until
G6 (Section 20 hard stop unchanged).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import shapely
from shapely.geometry import LineString, MultiLineString
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from app.connectors.dcm_street_centerline_geometry import (
    EXPECTED_LATEST_WKID as _DCM_EXPECTED_LATEST_WKID,
)
from app.connectors.dcm_street_centerline_geometry import (
    EXPECTED_WKID as _DCM_EXPECTED_WKID,
)
from app.connectors.dcm_street_centerline_geometry import (
    GEOMETRY_OK,
    SegmentPolyline,
)
from app.connectors.mappluto_geometry_arcgis import (
    EXPECTED_LATEST_WKID as _MAPPLUTO_EXPECTED_LATEST_WKID,
)
from app.connectors.mappluto_geometry_arcgis import (
    EXPECTED_WKID as _MAPPLUTO_EXPECTED_WKID,
)
from app.connectors.mappluto_geometry_arcgis import (
    GEOMETRY_REPAIRED,
    GEOMETRY_VALID,
    PINNED_GEOS_VERSION_STRING,
    PINNED_SHAPELY_VERSION,
    GeometryAssessment,
    canonical_to_shapely,
)

__all__ = [
    "BUFFER_FT",
    "BUFFER_FT_CITATION",
    "BUFFER_QUAD_SEGS",
    "CRS_STAMP",
    "EC2_UNDER_CLAIM_NOTICE",
    "EXPECTED_LATEST_WKID",
    "EXPECTED_WKID",
    "NO_WIDE_SEGMENTS_NOTICE",
    "STATUS_COMPUTED",
    "STATUS_NO_WIDE_SEGMENTS_PROVIDED",
    "STATUS_PRECONDITIONS_NOT_ATTESTED",
    "TANGENCY_NOTICE",
    "AttestedLotPolygon",
    "AttestedWideSegment",
    "Ec5AttestedPreconditions",
    "InvalidGeometryError",
    "MalformedAttestationError",
    "SegmentContribution",
    "WideStreetBufferEngineError",
    "WideStreetBufferResult",
    "WrongCRSError",
    "compute_wide_street_buffer_intersection",
]

# ---------------------------------------------------------------------------
# CRS identity: both accepted connectors resolve the SAME authoritative pair
# (research Part 2.3: "Both source geometries share the identical CRS - no
# reprojection is required"). Asserted at import time rather than assumed -
# if either accepted connector's own pin ever drifted, this fails loudly
# instead of silently buffering across an unnoticed CRS mismatch.
# ---------------------------------------------------------------------------
assert _DCM_EXPECTED_WKID == _MAPPLUTO_EXPECTED_WKID, (
    "DCM and MapPLUTO accepted connectors no longer agree on wkid - "
    "the research Part 2.3 same-CRS simplification no longer holds"
)
assert _DCM_EXPECTED_LATEST_WKID == _MAPPLUTO_EXPECTED_LATEST_WKID, (
    "DCM and MapPLUTO accepted connectors no longer agree on latestWkid - "
    "the research Part 2.3 same-CRS simplification no longer holds"
)

EXPECTED_WKID = _DCM_EXPECTED_WKID
EXPECTED_LATEST_WKID = _DCM_EXPECTED_LATEST_WKID
CRS_STAMP = {
    "wkid": EXPECTED_WKID,
    "latest_wkid": EXPECTED_LATEST_WKID,
    "authority": "EPSG:2263 (NAD83 / New York Long Island, US survey feet)",
}

# ---------------------------------------------------------------------------
# The 100-ft buffer constant and its citation (contract item 5).
# ---------------------------------------------------------------------------
BUFFER_FT = 100.0
BUFFER_FT_CITATION = (
    "ZR 23-22 footnote 1: \"For zoning lots, or portions thereof, located "
    "within 100 feet of a wide street.\" (research report "
    "project-control/reports/M4-T016-a2-geometry-mechanics-research.md "
    "Part 2.1, quoted verbatim)."
)

# Buffer arc-approximation resolution. The buffer call below uses
# ``BaseGeometry.buffer`` (the shapely method invoked on a shapely geometry
# instance, e.g. ``linework.buffer(...)``), NOT the different top-level
# ``shapely.buffer()`` function - the two have DIFFERENT defaults
# (``BaseGeometry.buffer`` defaults to quad_segs=16; the unused top-level
# ``shapely.buffer()`` defaults to quad_segs=8; verified live via
# ``inspect.signature`` against installed shapely 2.0.7, per the G3 rework
# ruling). This module pins 16 explicitly - set for determinism (an
# explicit, permanent value rather than an implicit library default that
# could change across shapely versions) and it matches the real default of
# the API actually called here, so there is no silent divergence from the
# library's own behavior. Higher quad_segs -> a finer arc approximation
# (more vertices per quarter circle); this matters at a segment's rounded
# end cap, not along its straight sides (see the end-cap-proximate test).
BUFFER_QUAD_SEGS = 16

# ---------------------------------------------------------------------------
# Result states (EC-6: a distinct typed state, never a computed default).
# ---------------------------------------------------------------------------
STATUS_COMPUTED = "computed"
STATUS_NO_WIDE_SEGMENTS_PROVIDED = "no_wide_segments_provided"
STATUS_PRECONDITIONS_NOT_ATTESTED = "preconditions_not_attested"

NO_WIDE_SEGMENTS_NOTICE = (
    "EC-6 (research Part 2.4 item 6): no wide-disposed DCM segment was "
    "supplied for this lot. This is a distinct, honest outcome - NOT a "
    "computed False (the lot may or may not actually be within 100 ft of a "
    "real wide street; this module was simply given nothing to test "
    "against) and NOT a computed True. Never defaulted either way."
)

TANGENCY_NOTICE = (
    "EC-4 (research Part 2.4 item 4): intersects/intersection below are "
    "GEOS's UNMODIFIED literal result at the exact 100.0-ft buffer boundary "
    "- no tolerance is added or subtracted anywhere in this module. "
    "mappluto_geometry_arcgis.BOUNDARY_TOLERANCE_FT (20.0 ft) is a "
    "POSITIONAL-ACCURACY constant for the MapPLUTO source survey, not a "
    "legal buffer allowance, and is deliberately NOT referenced here. "
    "Whether a legal tolerance should apply at exact tangency is an OPEN, "
    "UNRESOLVED question left to G6 qualified legal review; this module "
    "does not invent one."
)

EC2_UNDER_CLAIM_NOTICE = (
    "EC-2 (research Part 2.4 item 2): this module only ever sees the "
    "caller's wide-only input contract - segments the accepted M4-T015 "
    "classifier / M4-T019 policy already resolved to "
    "effective_disposition == 'wide'. A segment left ambiguous "
    "(range_straddles_cutoff, approximate_or_hedged_value_ambiguous, "
    "width_irregular, etc.) never reaches this module and is therefore "
    "EXCLUDED from every buffer/union computed here. A lot genuinely within "
    "100 ft of what might be a real wide street, whose DCM reading was "
    "merely messy, is conservatively scored as not-within-100-ft. This is "
    "an honest under-claim consistent with the project's fail-closed "
    "posture, not a defect of this module."
)


# ---------------------------------------------------------------------------
# Typed errors
# ---------------------------------------------------------------------------
class WideStreetBufferEngineError(Exception):
    """Base typed error. Payloads never contain stack traces or secrets (no
    network I/O occurs in this module; there is nothing to leak)."""

    error_type = "wide_street_buffer_engine_error"

    def __init__(self, message: str, *, correlation_id: str, detail: dict | None = None):
        super().__init__(message)
        self.message = message
        self.correlation_id = correlation_id
        self.detail = detail or {}

    def to_payload(self) -> dict:
        return {
            "error_type": self.error_type,
            "message": self.message,
            "correlation_id": self.correlation_id,
            "detail": self.detail,
        }


class WrongCRSError(WideStreetBufferEngineError):
    """A geometry input's CRS identity is absent or does not match the
    authoritative EPSG:2263 pair. There is no reprojection path - this is
    always a refusal, never a computed number."""

    error_type = "wrong_crs"


class InvalidGeometryError(WideStreetBufferEngineError):
    """A geometry input is degenerate, invalid, or not in a usable state
    (segment status != GEOMETRY_OK; lot assessment.status not in
    {valid, repaired})."""

    error_type = "invalid_geometry"


class MalformedAttestationError(WideStreetBufferEngineError):
    """The EC-5 attestation input is missing, of the wrong type, or carries
    a field of the wrong type. A caller can never satisfy this precondition
    by accident - only by explicit, typed, correctly-shaped construction."""

    error_type = "malformed_attestation"


# ---------------------------------------------------------------------------
# Typed inputs (no defaults anywhere - see docstrings; mirrors the accepted
# dcm_street_width_policy.AttestedPreconditions precedent).
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Ec5AttestedPreconditions:
    """EC-5 (research Part 2.4 item 5): the named-street override and the
    C5-3/C6-4/C6-6 alternate-width clause are OUT of this module's scope
    (B7 wires them later). Every field is required with NO default - a
    caller must explicitly construct this, so the omission can never be
    silent (S2). This module does NOT gate computation on the attested
    values (see module docstring) - it only forces explicit acknowledgment
    and carries the attestation through every result for audit.

    ``named_street_override_checked`` - the caller checked whether either of
    the two named-street legislative designations (Broadway W94-97 CD7;
    Allen St Rivington-Delancey CD3) applies to any excluded segment near
    this lot.
    ``alternate_width_clause_checked`` - the caller checked whether the
    C5-3/C6-4/C6-6 alternate-width clause applies.
    ``attestation_note`` - free-form provenance for the above (who/what
    checked, or why the check was not yet possible); required (may be
    explicitly ``None`` - never omitted).
    """

    named_street_override_checked: bool
    alternate_width_clause_checked: bool
    attestation_note: str | None


@dataclass(frozen=True)
class AttestedWideSegment:
    """One caller-attested wide-disposed DCM segment, ready for buffering.

    The caller MUST have already filtered to effective_disposition == 'wide'
    via the accepted M4-T015 classifier / M4-T019 policy - this module never
    re-classifies width and never re-checks disposition.

    ``polyline`` - the accepted M4-T020 ``SegmentPolyline`` (status must be
    ``GEOMETRY_OK``; anything else is the typed ``InvalidGeometryError``).
    ``wkid`` / ``latest_wkid`` - this segment's OWN validated CRS identity
    (from its source ``SegmentGeometryPage``), required with NO default so a
    segment can never be interpreted under an assumed or borrowed CRS.
    ``classification_basis`` - free-form passthrough naming WHY this segment
    was judged wide (e.g. the M4-T015 ``WidthClassification.basis`` plus the
    connector's ``effective_disposition``) - carried to the result for
    provenance; never interpreted or re-decided by this module.
    ``source_retrieved_at`` / ``source_raw_digest`` - retrieval-identity and
    raw-body-digest provenance passthrough, required with no default (may be
    explicitly ``None`` when genuinely unavailable - never omitted).
    """

    polyline: SegmentPolyline
    wkid: int | None
    latest_wkid: int | None
    classification_basis: str
    source_retrieved_at: str | None
    source_raw_digest: str | None


@dataclass(frozen=True)
class AttestedLotPolygon:
    """The MapPLUTO zoning-lot polygon measurement surface.

    ``assessment`` - the accepted ``mappluto_geometry_arcgis.GeometryAssessment``
    (status must be ``valid`` or ``repaired``; ``invalid_geometry`` /
    ``review_required`` is the typed ``InvalidGeometryError`` here).
    ``wkid`` / ``latest_wkid`` - the lot geometry's OWN validated CRS
    identity, required with NO default (independently re-validated here,
    never trusted merely because ``assessment`` exists).
    ``lot_identity`` - a caller-chosen stable label (e.g. formatted BBL) for
    the result's provenance.
    ``source_retrieved_at`` / ``source_raw_digest`` - retrieval-identity and
    raw-body-digest provenance passthrough, required with no default.
    """

    assessment: GeometryAssessment
    wkid: int | None
    latest_wkid: int | None
    lot_identity: str
    source_retrieved_at: str | None
    source_raw_digest: str | None


# ---------------------------------------------------------------------------
# Typed results
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SegmentContribution:
    """One wide segment's own buffer/intersection contribution (EC-1/EC-3:
    always visible individually, never collapsed into the aggregate).

    ``segment_source_retrieved_at`` / ``segment_source_raw_digest`` - the
    originating ``AttestedWideSegment``'s retrieval-identity/raw-digest
    provenance, carried through unmodified (G4-F1 rework: previously
    required on the input but silently dropped before reaching any output;
    now threaded through so a result can be traced to the fetch that
    produced it, per CLAUDE.md permanent principle 2)."""

    segment_object_id: int | None
    classification_basis: str
    buffer_geometry: BaseGeometry
    intersects: bool
    sub_geometry: BaseGeometry
    area_sq_ft: float
    segment_source_retrieved_at: str | None
    segment_source_raw_digest: str | None


@dataclass(frozen=True)
class WideStreetBufferResult:
    """Complete result of one lot's wide-street buffer/intersection
    computation (or a typed non-computed outcome: EC-6 empty-set, or EC-5
    preconditions-not-attested per the rework ruling RULING 1).

    ``status`` is ``STATUS_COMPUTED``, ``STATUS_NO_WIDE_SEGMENTS_PROVIDED``,
    or ``STATUS_PRECONDITIONS_NOT_ATTESTED`` - every non-``STATUS_COMPUTED``
    value leaves every buffer/intersection field ``None``/empty by
    construction, never a manufactured True or False (EC-6) and never a
    computed-looking number on unverified legal preconditions (EC-5).
    ``segment_contributions`` carries EVERY qualifying segment's own result
    (EC-1/EC-3); ``aggregate_*`` fields carry the union-before-intersect
    result (EC-1). ``ec5_preconditions`` is always the caller's attestation,
    passed through unmodified regardless of status. ``tangency_notice`` /
    ``ec2_under_claim_notice`` are always present (EC-4/EC-2 documentation,
    never conditional on the outcome); ``empty_notice`` is populated only
    when ``status`` is ``STATUS_NO_WIDE_SEGMENTS_PROVIDED``;
    ``ec5_not_attested_notice`` is populated only when ``status`` is
    ``STATUS_PRECONDITIONS_NOT_ATTESTED``.

    ``lot_source_retrieved_at`` / ``lot_source_raw_digest`` - the
    originating ``AttestedLotPolygon``'s retrieval-identity/raw-digest
    provenance, carried through unmodified on EVERY status (the lot is
    validated before either the EC-5 gate or the EC-6 empty check, so its
    provenance is always known where the lot itself was resolvable; G4-F1
    rework - see ``SegmentContribution`` for the per-segment counterpart).
    """

    status: str
    buffer_ft: float
    buffer_ft_citation: str
    lot_identity: str
    lot_area_sq_ft: float | None
    segment_contributions: tuple[SegmentContribution, ...]
    aggregate_union_buffer: BaseGeometry | None
    aggregate_intersects: bool | None
    aggregate_sub_geometry: BaseGeometry | None
    aggregate_area_sq_ft: float | None
    crs: dict
    shapely_version: str
    geos_version: str
    ec5_preconditions: Ec5AttestedPreconditions
    tangency_notice: str
    ec2_under_claim_notice: str
    empty_notice: str | None
    ec5_not_attested_notice: str | None
    lot_source_retrieved_at: str | None
    lot_source_raw_digest: str | None


# ---------------------------------------------------------------------------
# Internal validation helpers
# ---------------------------------------------------------------------------
def _require_crs(
    wkid: object, latest_wkid: object, *, label: str, correlation_id: str
) -> None:
    """The CRS gate: geometry is interpreted ONLY under the authoritative
    EPSG:2263 pair (wkid 102718 / latestWkid 2263). Anything else, or an
    absent (``None``) value, is the typed refusal naming expected vs
    received. There is no reprojection path - a wrong or unknown CRS is
    NEVER assumed or corrected."""
    if wkid == EXPECTED_WKID and latest_wkid == EXPECTED_LATEST_WKID:
        return
    raise WrongCRSError(
        f"{label} does not carry the authoritative EPSG:2263 identity "
        f"(expected wkid {EXPECTED_WKID} / latestWkid {EXPECTED_LATEST_WKID}; "
        f"received wkid={wkid!r} / latestWkid={latest_wkid!r}); geometry in "
        "an absent, mismatched, or unrecognized CRS is never interpreted, "
        "assumed, or reprojected - no reprojection code path exists in this "
        "module",
        correlation_id=correlation_id,
        detail={
            "label": label,
            "expected": {"wkid": EXPECTED_WKID, "latestWkid": EXPECTED_LATEST_WKID},
            "received": {"wkid": wkid, "latestWkid": latest_wkid},
        },
    )


def _validate_ec5_preconditions(
    preconditions: Ec5AttestedPreconditions, *, correlation_id: str
) -> None:
    if not isinstance(preconditions, Ec5AttestedPreconditions):
        raise MalformedAttestationError(
            "ec5_preconditions must be an Ec5AttestedPreconditions instance "
            f"(received {type(preconditions).__name__}); a bare bool or dict "
            "cannot silently satisfy this precondition",
            correlation_id=correlation_id,
            detail={"received_type": type(preconditions).__name__},
        )
    bad_fields = [
        name
        for name, value in (
            ("named_street_override_checked", preconditions.named_street_override_checked),
            ("alternate_width_clause_checked", preconditions.alternate_width_clause_checked),
        )
        if not isinstance(value, bool)
    ]
    if bad_fields:
        raise MalformedAttestationError(
            "ec5_preconditions carries a non-boolean value for: "
            f"{', '.join(bad_fields)}; each attestation must be an explicit "
            "True/False, never a truthy/falsy stand-in",
            correlation_id=correlation_id,
            detail={"bad_fields": bad_fields},
        )


def _ec5_precondition_failures(preconditions: Ec5AttestedPreconditions) -> tuple[str, ...]:
    """Return the human-readable reasons EC-5 computation must be refused,
    or an empty tuple when both preconditions are affirmatively attested.
    Mirrors ``dcm_street_width_policy._precondition_failures`` (the accepted
    D-052/M4-T019 precedent this task packet names by name): no precondition
    is ever treated as satisfied by omission or by a truthy stand-in - both
    fields are explicitly re-checked here (per RULING 1,
    ``project-control/reports/M4-T021-rework-ruling.md``)."""
    failures: list[str] = []
    if not preconditions.named_street_override_checked:
        failures.append(
            "named_street_override_checked is False - the Broadway W94-97 "
            "CD7 / Allen St Rivington-Delancey CD3 named-street override has "
            "not been checked for this lot's excluded segments"
        )
    if not preconditions.alternate_width_clause_checked:
        failures.append(
            "alternate_width_clause_checked is False - the C5-3/C6-4/C6-6 "
            "alternate-width clause has not been checked for this lot"
        )
    return tuple(failures)


def _segment_linework(
    polyline: SegmentPolyline, *, correlation_id: str
) -> MultiLineString:
    """Build the segment's full linework (ALL its paths - a segment can
    carry multiple disjoint paths per the accepted M4-T020 fixture evidence)
    as one MultiLineString, ready to buffer as a single operation (EC-3:
    always per-segment)."""
    if polyline.status != GEOMETRY_OK or not polyline.paths:
        raise InvalidGeometryError(
            "wide-disposed segment does not carry usable OK geometry "
            f"(status={polyline.status!r}); this module never buffers a "
            "degenerate, invalid, or absent polyline",
            correlation_id=correlation_id,
            detail={"status": polyline.status, "object_id": polyline.object_id},
        )
    return MultiLineString([LineString(path) for path in polyline.paths])


def _lot_shapely(
    assessment: GeometryAssessment, *, correlation_id: str
) -> BaseGeometry:
    """Rebuild the lot's shapely geometry via the accepted
    ``canonical_to_shapely`` (read-only reuse - never re-implemented here).
    Only ``valid``/``repaired`` assessments carry usable geometry;
    ``invalid_geometry``/``review_required`` is the typed refusal."""
    if assessment.status not in (GEOMETRY_VALID, GEOMETRY_REPAIRED):
        raise InvalidGeometryError(
            "lot polygon assessment is not a usable valid/repaired geometry "
            f"(status={assessment.status!r}); this module never buffers "
            "against an invalid_geometry/review_required lot",
            correlation_id=correlation_id,
            detail={"status": assessment.status, "findings": list(assessment.findings)},
        )
    if assessment.canonical_geometry is None:
        # Unreachable given the accepted connector's own invariant (valid/
        # repaired always populates canonical_geometry) - kept as a typed
        # guard so a future drift in that invariant can never pass silently.
        raise InvalidGeometryError(
            "lot polygon assessment is valid/repaired but carries no "
            "canonical_geometry (accepted-connector invariant guard)",
            correlation_id=correlation_id,
            detail={"status": assessment.status},
        )
    return canonical_to_shapely(assessment.canonical_geometry)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def compute_wide_street_buffer_intersection(
    lot: AttestedLotPolygon,
    wide_segments: Sequence[AttestedWideSegment],
    *,
    ec5_preconditions: Ec5AttestedPreconditions,
    correlation_id: str,
) -> WideStreetBufferResult:
    """Compute the ZR 23-22 footnote 1 100-ft wide-street buffer/
    intersection for one lot against caller-supplied, already wide-disposed
    DCM segments (research Part 2.2 steps A-D).

    Order of operations: (1) EC-5 attestation is validated first for
    type/shape (a malformed/missing attestation refuses before any geometry
    is touched); (2) the lot's CRS identity and geometry validity are gated;
    (3) the EC-5 attestation is then gated on its VALUE (RULING 1,
    ``project-control/reports/M4-T021-rework-ruling.md``) - when either
    attested field is ``False``, computation refuses immediately with the
    typed ``STATUS_PRECONDITIONS_NOT_ATTESTED`` result, before any segment
    is ever touched; (4) an empty ``wide_segments`` sequence returns the
    typed EC-6 result immediately; (5) each segment's CRS identity and
    geometry validity are gated, its 100-ft buffer computed, and its own
    intersects/intersection recorded (EC-1/EC-3); (6) all segment buffers
    are unioned (``unary_union``) BEFORE intersecting the lot for the
    aggregate result (EC-1). No coordinate is ever interpreted, and no
    buffer is ever computed, outside the validated EPSG:2263 CRS, and no
    buffer is ever computed against unattested EC-5 preconditions.
    """
    _validate_ec5_preconditions(ec5_preconditions, correlation_id=correlation_id)

    _require_crs(lot.wkid, lot.latest_wkid, label="lot polygon", correlation_id=correlation_id)
    lot_geometry = _lot_shapely(lot.assessment, correlation_id=correlation_id)
    lot_area_sq_ft = lot.assessment.area_sq_ft

    ec5_failures = _ec5_precondition_failures(ec5_preconditions)
    if ec5_failures:
        reason = (
            "EC-5 (research Part 2.4 item 5): computation refused - the "
            "named-street override / alternate-width-clause preconditions "
            "are not affirmatively attested: " + "; ".join(ec5_failures) + ". "
            "Mirrors the accepted D-052/M4-T019 AttestedPreconditions "
            "precedent (dcm_street_width_policy.classify_street_width_policy's "
            "DECISION_UNRESOLVED gate on its analogous exceptions_checked "
            "attestation) - never silently computed on unverified legal "
            "preconditions."
        )
        return WideStreetBufferResult(
            status=STATUS_PRECONDITIONS_NOT_ATTESTED,
            buffer_ft=BUFFER_FT,
            buffer_ft_citation=BUFFER_FT_CITATION,
            lot_identity=lot.lot_identity,
            lot_area_sq_ft=lot_area_sq_ft,
            segment_contributions=(),
            aggregate_union_buffer=None,
            aggregate_intersects=None,
            aggregate_sub_geometry=None,
            aggregate_area_sq_ft=None,
            crs=dict(CRS_STAMP),
            shapely_version=shapely.__version__,
            geos_version=shapely.geos_version_string,
            ec5_preconditions=ec5_preconditions,
            tangency_notice=TANGENCY_NOTICE,
            ec2_under_claim_notice=EC2_UNDER_CLAIM_NOTICE,
            empty_notice=None,
            ec5_not_attested_notice=reason,
            lot_source_retrieved_at=lot.source_retrieved_at,
            lot_source_raw_digest=lot.source_raw_digest,
        )

    if len(wide_segments) == 0:
        return WideStreetBufferResult(
            status=STATUS_NO_WIDE_SEGMENTS_PROVIDED,
            buffer_ft=BUFFER_FT,
            buffer_ft_citation=BUFFER_FT_CITATION,
            lot_identity=lot.lot_identity,
            lot_area_sq_ft=lot_area_sq_ft,
            segment_contributions=(),
            aggregate_union_buffer=None,
            aggregate_intersects=None,
            aggregate_sub_geometry=None,
            aggregate_area_sq_ft=None,
            crs=dict(CRS_STAMP),
            shapely_version=shapely.__version__,
            geos_version=shapely.geos_version_string,
            ec5_preconditions=ec5_preconditions,
            tangency_notice=TANGENCY_NOTICE,
            ec2_under_claim_notice=EC2_UNDER_CLAIM_NOTICE,
            empty_notice=NO_WIDE_SEGMENTS_NOTICE,
            ec5_not_attested_notice=None,
            lot_source_retrieved_at=lot.source_retrieved_at,
            lot_source_raw_digest=lot.source_raw_digest,
        )

    contributions: list[SegmentContribution] = []
    buffers: list[BaseGeometry] = []
    for segment in wide_segments:
        label = f"segment object_id={segment.polyline.object_id!r}"
        _require_crs(segment.wkid, segment.latest_wkid, label=label, correlation_id=correlation_id)
        linework = _segment_linework(segment.polyline, correlation_id=correlation_id)
        buffer_geometry = linework.buffer(BUFFER_FT, quad_segs=BUFFER_QUAD_SEGS)
        buffers.append(buffer_geometry)
        intersects = bool(lot_geometry.intersects(buffer_geometry))
        sub_geometry = lot_geometry.intersection(buffer_geometry)
        contributions.append(
            SegmentContribution(
                segment_object_id=segment.polyline.object_id,
                classification_basis=segment.classification_basis,
                buffer_geometry=buffer_geometry,
                intersects=intersects,
                sub_geometry=sub_geometry,
                area_sq_ft=float(sub_geometry.area),
                segment_source_retrieved_at=segment.source_retrieved_at,
                segment_source_raw_digest=segment.source_raw_digest,
            )
        )

    union_buffer = unary_union(buffers)
    aggregate_intersects = bool(lot_geometry.intersects(union_buffer))
    aggregate_sub_geometry = lot_geometry.intersection(union_buffer)

    return WideStreetBufferResult(
        status=STATUS_COMPUTED,
        buffer_ft=BUFFER_FT,
        buffer_ft_citation=BUFFER_FT_CITATION,
        lot_identity=lot.lot_identity,
        lot_area_sq_ft=lot_area_sq_ft,
        segment_contributions=tuple(contributions),
        aggregate_union_buffer=union_buffer,
        aggregate_intersects=aggregate_intersects,
        aggregate_sub_geometry=aggregate_sub_geometry,
        aggregate_area_sq_ft=float(aggregate_sub_geometry.area),
        crs=dict(CRS_STAMP),
        shapely_version=shapely.__version__,
        geos_version=shapely.geos_version_string,
        ec5_preconditions=ec5_preconditions,
        tangency_notice=TANGENCY_NOTICE,
        ec2_under_claim_notice=EC2_UNDER_CLAIM_NOTICE,
        empty_notice=None,
        ec5_not_attested_notice=None,
        lot_source_retrieved_at=lot.source_retrieved_at,
        lot_source_raw_digest=lot.source_raw_digest,
    )


# Determinism assertions (contract item 5, pyproject discipline): the
# INSTALLED shapely/GEOS build must match the accepted mappluto_geometry_arcgis
# pins (PINNED_SHAPELY_VERSION = "2.0.7" / PINNED_GEOS_VERSION_STRING =
# "3.11.4") - asserted at import time so an unnoticed environment drift
# fails closed immediately rather than silently producing geometry whose
# exact numeric output is no longer proven reproducible. Re-asserted in the
# test suite (test_shapely_and_geos_versions_are_pinned_for_determinism).
assert shapely.__version__ == PINNED_SHAPELY_VERSION, (
    f"installed shapely {shapely.__version__} does not match the accepted "
    f"pin {PINNED_SHAPELY_VERSION} - geometry determinism is not proven "
    "for this build"
)
assert shapely.geos_version_string == PINNED_GEOS_VERSION_STRING, (
    f"installed GEOS {shapely.geos_version_string} does not match the "
    f"accepted pin {PINNED_GEOS_VERSION_STRING} - geometry determinism is "
    "not proven for this build"
)
