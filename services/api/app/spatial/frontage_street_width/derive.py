"""Street width per frontage: the pure entry point (queue item B-04, plan M1-13 and §4).

For each frontage the B-03 site geometry found, take the DCM street center-line segments it
was matched to and read their MAPPED width (DCM ``Streetwidth`` - the City Map width zoning
uses; LION / Geoclient widths are paved widths and are never read here). Each segment goes
through the accepted classifier (:mod:`app.connectors.dcm_street_width_classifier`) and the
accepted D-052 policy (:mod:`app.connectors.dcm_street_width_policy`), with attestations
that state only what was actually established:

* source documented - the segment's retrieval (source id, URL, time, body sha256) is on record;
* street status - the segment is a currently mapped street with no special City Map flag;
* frontage coverage - B-03 confirmed the frontage (every sample along every fronting lot line
  sits on this street's street line and the street data is complete); anything less is not
  coverage;
* exceptions - both ZR 12-10 exception checks returned ``not_applicable`` (``exceptions.py``).

A frontage is ``wide`` / ``narrow`` only when the policy issues that class for every segment
along it. Otherwise it is marked "Needs street width" with the reasons and both classes as
possible - never a silent narrow default (D-051: narrow is not always the safe side).

Pure and deterministic: no network, no flags, no callers yet (a later Lane A/C task wires
it into the results).
"""

from __future__ import annotations

from collections.abc import Iterable

from app.connectors.dcm_street_width_classifier import classify_street_width
from app.connectors.dcm_street_width_policy import (
    DECISION_NARROW,
    DECISION_WIDE,
    DRAFT_LABEL_NOTICE,
    FRONTAGE_MATCH_COVERAGE_ESTABLISHED,
    AttestedPreconditions,
    classify_street_width_policy,
)
from app.spatial.site_geometry.adjacency import mapped_width_ft
from app.spatial.site_geometry.labels import SourcedValue, city_records_value, unknown_value
from app.spatial.site_geometry.results import (
    FRONTAGE_CONFIRMED,
    STATUS_REFUSED,
    SiteGeometry,
    StreetFrontage,
)

from .exceptions import (
    EXCEPTION_NOT_APPLICABLE,
    ExceptionCheck,
    Zr1210Exceptions,
    default_exceptions,
)
from .inputs import LotZoningContext, MappedStreetSegment
from .results import (
    CLASS_NARROW,
    CLASS_NEEDS_STREET_WIDTH,
    CLASS_WIDE,
    MARKER_NEEDS_STREET_WIDTH,
    STATUS_COMPLETE,
    STATUS_NEEDS_STREET_WIDTH,
    FrontageStreetWidth,
    SegmentWidthReading,
    SiteStreetWidths,
)

__all__ = ["FRONTAGE_NOT_CONFIRMED", "METHOD_VERSION", "derive_frontage_street_widths"]

METHOD_VERSION = "frontage-street-width-1"

# Attested frontage-match method when B-03 did not confirm the frontage. Any value other
# than coverage_established fails the D-052 coverage precondition (R002); this one says why.
FRONTAGE_NOT_CONFIRMED = "site_geometry_frontage_not_confirmed"

_BOTH = (CLASS_WIDE, CLASS_NARROW)


def _label(segment: MappedStreetSegment) -> str:
    return f"{segment.street_name or 'Unnamed street'} (City Map segment {segment.object_id})"


def _reading(segment: MappedStreetSegment, coverage: bool, alternate: ExceptionCheck,
             exceptions: Zr1210Exceptions, community_district: int | None
             ) -> SegmentWidthReading:
    named = exceptions.named_street(segment, community_district)
    classification = classify_street_width(segment.mapped_width_raw)
    source = segment.source
    preconditions = AttestedPreconditions(
        source_documented=source.documented,
        source_version=source.dataset_version or source.retrieved_at,
        street_status_checked=segment.plain_mapped_street,
        frontage_match_method=(FRONTAGE_MATCH_COVERAGE_ESTABLISHED if coverage
                               else FRONTAGE_NOT_CONFIRMED),
        matched_geometry_ref=f"DCM OBJECTID={segment.object_id}",
        exceptions_checked=(alternate.status == EXCEPTION_NOT_APPLICABLE
                            and named.status == EXCEPTION_NOT_APPLICABLE),
    )
    decision = classify_street_width_policy(classification, preconditions)
    return SegmentWidthReading(segment, classification, named, decision)


def _width_reason(reading: SegmentWidthReading) -> str | None:
    bounds = reading.decision.interpreted_bounds
    raw = reading.segment.mapped_width_raw
    if not bounds.derivable:
        return (f"{_label(reading.segment)}: the mapped width {raw!r} gives no usable width "
                f"({bounds.interval_description})")
    if not bounds.one_sided:
        return (f"{_label(reading.segment)}: the mapped width {raw!r} allows widths on both "
                f"sides of 75 ft ({bounds.interval_description})")
    return None


def _segment_reasons(reading: SegmentWidthReading) -> list[str]:
    segment = reading.segment
    reasons = []
    if not segment.plain_mapped_street:
        reasons.append(f"{_label(segment)}: {segment.status_note or 'not a plain mapped street'}")
    if not segment.source.documented:
        reasons.append(f"{_label(segment)}: its retrieval (URL, time, sha256) is not on record")
    width = _width_reason(reading)
    if width:
        reasons.append(width)
    if reading.named_street.status != EXCEPTION_NOT_APPLICABLE:
        reasons.append(f"{reading.named_street.provision}: {reading.named_street.reason}")
    return reasons


def _listing(readings: tuple[SegmentWidthReading, ...]) -> str:
    return ", ".join(f"{r.segment.mapped_width_raw!r} (segment {r.segment.object_id})"
                     for r in readings)


def _mapped_width(frontage: StreetFrontage, readings: tuple[SegmentWidthReading, ...],
                  coverage: bool) -> SourcedValue:
    if not readings:
        return unknown_value("ft", "No City Map street center line was matched to this "
                             "frontage.")
    times = sorted({r.segment.source.retrieved_at or "unknown time" for r in readings})
    ids = ", ".join(str(r.segment.object_id) for r in readings)
    basis = (f"DCP Digital City Map mapped width (Streetwidth) of segment(s) {ids}, "
             f"retrieved {', '.join(times)}")
    if not coverage:
        return unknown_value("ft", f"The frontage on {frontage.street_name} is not "
                             "confirmed.", basis)
    values = {mapped_width_ft(r.segment.mapped_width_raw) for r in readings}
    if len(values) == 1 and None not in values:
        return city_records_value(next(iter(values)), "ft", basis)
    if None in values:
        return unknown_value("ft", f"The mapped width is not one number: {_listing(readings)}.",
                             basis)
    return unknown_value("ft", f"The mapped width changes along this frontage: "
                         f"{_listing(readings)}.", basis)


def _street_class(readings: tuple[SegmentWidthReading, ...]) -> str:
    states = {r.decision.decision_state for r in readings}
    if readings and states == {DECISION_WIDE}:
        return CLASS_WIDE
    if readings and states == {DECISION_NARROW}:
        return CLASS_NARROW
    return CLASS_NEEDS_STREET_WIDTH


def _reasons(frontage: StreetFrontage, readings: tuple[SegmentWidthReading, ...],
             missing: list[int], clashing: list[int], coverage: bool,
             alternate: ExceptionCheck) -> list[str]:
    """Every reason this frontage cannot take a class, in plain words (empty = none)."""
    reasons: list[str] = []
    if not frontage.segment_object_ids:
        reasons.append("No City Map street center line was matched to this frontage.")
    if missing:
        reasons.append("City Map segment(s) " + ", ".join(map(str, missing))
                       + " matched to this frontage are not in the street data given.")
    if clashing:
        reasons.append("The street data gives conflicting records for City Map segment(s) "
                       + ", ".join(map(str, clashing)) + ".")
    given = {r.segment.mapped_width_raw for r in readings} - {None}
    if not missing and not clashing and given != set(frontage.mapped_width_raw):
        reasons.append("The street data given differs from the data the frontage was "
                       "measured with.")
    if not coverage:
        reasons.append(f"The frontage on {frontage.street_name} is not confirmed: "
                       f"{frontage.length.reason or 'see the site geometry'}")
    if alternate.status != EXCEPTION_NOT_APPLICABLE:
        reasons.append(f"{alternate.provision}: {alternate.reason}")
    for reading in readings:
        reasons.extend(_segment_reasons(reading))
    states = {r.decision.decision_state for r in readings}
    if {DECISION_WIDE, DECISION_NARROW} <= states:
        reasons.append(f"The mapped width changes along this frontage ({_listing(readings)}): "
                       "part is wide and part is narrow.")
    return reasons


def _frontage(frontage: StreetFrontage, by_id: dict[int, MappedStreetSegment],
              conflicting: set[int], alternate: ExceptionCheck, exceptions: Zr1210Exceptions,
              community_district: int | None) -> FrontageStreetWidth:
    coverage = frontage.status == FRONTAGE_CONFIRMED
    missing = [i for i in frontage.segment_object_ids if i not in by_id]
    clashing = [i for i in frontage.segment_object_ids if i in conflicting]
    segments = tuple(by_id[i] for i in frontage.segment_object_ids
                     if i in by_id and i not in conflicting)
    readings = tuple(_reading(s, coverage, alternate, exceptions, community_district)
                     for s in segments)
    reasons = _reasons(frontage, readings, missing, clashing, coverage, alternate)
    street_class = CLASS_NEEDS_STREET_WIDTH if reasons else _street_class(readings)
    if street_class == CLASS_NEEDS_STREET_WIDTH and not reasons:
        reasons.extend(r.decision.classification_reason for r in readings)
    sources = tuple(dict.fromkeys(r.segment.source for r in readings))
    needs = street_class == CLASS_NEEDS_STREET_WIDTH
    return FrontageStreetWidth(
        street_key=frontage.street_key,
        street_name=frontage.street_name,
        frontage_status=frontage.status,
        street_class=street_class,
        marker=MARKER_NEEDS_STREET_WIDTH if needs else None,
        possible_classes=_BOTH if needs else (street_class,),
        mapped_width=_mapped_width(frontage, readings, coverage),
        readings=readings,
        exceptions=(alternate, *(r.named_street for r in readings)),
        reasons=tuple(dict.fromkeys(reasons)) if needs else (),
        sources=sources,
        draft_label=DRAFT_LABEL_NOTICE,
    )


def _facts(segment: MappedStreetSegment) -> tuple:
    """A segment's City Map facts, without where they were read (the same segment may come
    back on two query pages)."""
    return (segment.street_name, segment.borough, segment.mapped_width_raw,
            segment.plain_mapped_street, segment.status_note)


def _index(segments: Iterable[MappedStreetSegment]):
    by_id: dict[int, MappedStreetSegment] = {}
    conflicting: set[int] = set()
    for segment in segments:
        known = by_id.get(segment.object_id)
        if known is not None and _facts(known) != _facts(segment):
            conflicting.add(segment.object_id)
        by_id.setdefault(segment.object_id, segment)
    return by_id, conflicting


def derive_frontage_street_widths(
    site: SiteGeometry,
    segments: Iterable[MappedStreetSegment],
    zoning: LotZoningContext | None = None,
    *,
    exceptions: Zr1210Exceptions | None = None,
) -> SiteStreetWidths:
    """Attach the mapped street width and class to every frontage of ``site``.

    ``segments`` are the DCM segments of the street data the site geometry was derived
    from (matched by OBJECTID). Never raises on bad data: gaps become "Needs street width".
    """
    exceptions = exceptions or default_exceptions()
    by_id, conflicting = _index(segments)
    alternate = exceptions.alternate_width(zoning)
    district = zoning.community_district if zoning else None
    frontages = tuple(_frontage(f, by_id, conflicting, alternate, exceptions, district)
                      for f in site.frontages)
    notes: list[str] = []
    if site.status == STATUS_REFUSED:
        notes.append(f"No frontage could be measured: {site.refusal_reason}")
    elif not frontages:
        notes.append("No street frontage was found in the City Map street data around the "
                     "lot, so no street width is attached.")
    needing = [f.street_name for f in frontages if f.needs_street_width]
    if needing:
        notes.append("Needs street width on " + ", ".join(needing) + ": show both the "
                     "wide-street and the narrow-street results until it is resolved.")
    complete = bool(frontages) and not needing
    return SiteStreetWidths(
        status=STATUS_COMPLETE if complete else STATUS_NEEDS_STREET_WIDTH,
        marker=None if complete else MARKER_NEEDS_STREET_WIDTH,
        frontages=frontages,
        notes=tuple(notes),
        draft_label=DRAFT_LABEL_NOTICE,
        provenance={
            "method_version": METHOD_VERSION,
            "site_geometry_method_version": site.parameters.get("method_version"),
            "width_source": "DCP Digital City Map street center line, Streetwidth "
                            "(mapped width)",
            "classifier": "app.connectors.dcm_street_width_classifier",
            "policy": "app.connectors.dcm_street_width_policy (D-052)",
            "zr_12_10_snapshot": {"snapshot_id": exceptions.snapshot_id,
                                  "content_digest_sha256": exceptions.snapshot_sha256},
            "zoning": ({"source": zoning.source, **dict(zoning.provenance)}
                       if zoning else None),
            "streets": site.provenance.get("streets"),
        },
    )
