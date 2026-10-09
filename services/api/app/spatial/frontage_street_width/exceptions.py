"""The ZR 12-10 "wide street" exceptions, checked before any width class issues (queue item
B-04; D-052-R001 "exceptions checked first").

ZR 12-10 (snapshot ``zr-12-10``, amended 2026-03-26) adds two ways a street can be a wide
street besides "75 feet or more in width":

* the C5-3 / C6-4 / C6-6 alternate-width clause (paragraph 1), and
* two streets named in Manhattan (Broadway in Community District 7, Allen Street in
  Community District 3; paragraph 2).

Both are read through the ACCEPTED matcher (:mod:`app.rules.named_street_override`); nothing
here interprets the ZR text. Each check is tri-state: ``not_applicable`` (checked, does not
apply), ``may_apply`` (a qualified reviewer must decide) or ``not_checked`` (an input is
missing). Only ``not_applicable`` on both lets the D-052 policy issue a class.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from app.connectors.dcm_street_centerline_arcgis import BOROUGH_DOMAIN

# ``_collapse`` is the matcher's own documented street/borough normalization, re-exported by
# the facade for its consumers; using it keeps the name test identical to the matcher's.
from app.rules.named_street_override import (
    SNAPSHOT_ID,
    MatchStatus,
    NamedStreetOverrideMatcher,
    OverrideQuery,
    _collapse,
)
from app.rules.snapshots import SnapshotStore

from .inputs import LotZoningContext, MappedStreetSegment

__all__ = [
    "EXCEPTION_MAY_APPLY",
    "EXCEPTION_NOT_APPLICABLE",
    "EXCEPTION_NOT_CHECKED",
    "PROVISION_ALTERNATE_WIDTH",
    "PROVISION_NAMED_STREET",
    "ExceptionCheck",
    "Zr1210Exceptions",
    "default_exceptions",
]

EXCEPTION_NOT_APPLICABLE = "not_applicable"
EXCEPTION_MAY_APPLY = "may_apply"
EXCEPTION_NOT_CHECKED = "not_checked"

PROVISION_ALTERNATE_WIDTH = "ZR 12-10 alternate-width clause (C5-3, C6-4, C6-6)"
PROVISION_NAMED_STREET = "ZR 12-10 streets named as wide"

# The matcher's alternate-width result for a district outside the clause.
_ALT_NOT_APPLICABLE = "not_applicable"

# The five borough names in the DCM connector's documented Borough domain. Only a segment in
# one of them, differing from every borough a named row gives, is cleared by borough; any
# other value (e.g. the domain's "CW") goes to the matcher.
_BOROUGH_NAMES = frozenset(
    _collapse(b) for b in BOROUGH_DOMAIN
    if b in ("Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"))


@dataclass(frozen=True)
class ExceptionCheck:
    provision: str
    status: str
    reason: str
    provision_id: str | None = None
    open_legal_questions: tuple[str, ...] = ()


def _not_checked(provision: str, reason: str) -> ExceptionCheck:
    return ExceptionCheck(provision, EXCEPTION_NOT_CHECKED, reason)


class Zr1210Exceptions:
    """Both ZR 12-10 exception checks over one validated snapshot.

    ``matcher`` is None when the snapshot could not be loaded; every check then reports
    ``not_checked`` with ``unavailable_reason``.
    """

    def __init__(self, matcher: NamedStreetOverrideMatcher | None,
                 named_rows: tuple[tuple[str, str], ...] = (),
                 snapshot_sha256: str | None = None,
                 unavailable_reason: str | None = None):
        self._matcher = matcher
        self._named_rows = named_rows
        self.snapshot_id = SNAPSHOT_ID
        self.snapshot_sha256 = snapshot_sha256
        self.unavailable_reason = unavailable_reason

    @classmethod
    def from_store(cls, store: SnapshotStore | None = None) -> Zr1210Exceptions:
        """Load from the snapshot store; raises when the snapshot cannot back the matcher."""
        snapshot = (store or SnapshotStore()).get(SNAPSHOT_ID)
        matcher = NamedStreetOverrideMatcher(snapshot)  # validates the snapshot fail-closed
        rows = snapshot.raw["named_street_overrides"]["rows"]
        named = tuple((str(row["borough"]), str(row["street_name"])) for row in rows)
        return cls(matcher, named, snapshot.content_digest_sha256)

    @classmethod
    def unavailable(cls, exc: BaseException) -> Zr1210Exceptions:
        return cls(None, unavailable_reason=(
            f"the ZR 12-10 snapshot could not be loaded ({type(exc).__name__})"))

    @classmethod
    def load(cls, store: SnapshotStore | None = None) -> Zr1210Exceptions:
        """Like :meth:`from_store`, but any load fault leaves every check not_checked."""
        try:
            return cls.from_store(store)
        except Exception as exc:  # noqa: BLE001 - fail-safe boundary: any load fault = unchecked
            return cls.unavailable(exc)

    def alternate_width(self, zoning: LotZoningContext | None) -> ExceptionCheck:
        """Is the lot in a C5-3 / C6-4 / C6-6 district? Needs the lot's zoning districts."""
        provision = PROVISION_ALTERNATE_WIDTH
        if self._matcher is None:
            return _not_checked(provision, self.unavailable_reason or "matcher unavailable")
        districts = tuple(d for d in (zoning.zoning_districts if zoning else ()) if d.strip())
        if not districts:
            return _not_checked(provision, "the lot's zoning districts are not known")
        results = [self._matcher.classify_alternate_width_district(d) for d in districts]
        applicable = [r for r in results if r.coverage_class != _ALT_NOT_APPLICABLE]
        if applicable:
            first = applicable[0]
            return ExceptionCheck(
                provision, EXCEPTION_MAY_APPLY,
                f"the lot is in {first.district}: {first.reason}",
                first.provision_id, tuple(first.open_legal_questions))
        listed = ", ".join(districts)
        return ExceptionCheck(
            provision, EXCEPTION_NOT_APPLICABLE,
            f"the lot's zoning districts in {zoning.source} ({listed}) are not C5-3, C6-4 or "
            "C6-6")

    def named_street(self, segment: MappedStreetSegment,
                     community_district: int | None) -> ExceptionCheck:
        """Is this segment one of the streets ZR 12-10 names as wide?"""
        provision = PROVISION_NAMED_STREET
        if self._matcher is None:
            return _not_checked(provision, self.unavailable_reason or "matcher unavailable")
        borough, street = segment.borough, segment.street_name
        if not (borough and borough.strip() and street and street.strip()):
            return _not_checked(provision, f"City Map segment {segment.object_id} has no "
                                "borough or street name")
        named = " and ".join(f"{s} ({b})" for b, s in self._named_rows)
        boroughs = {_collapse(b) for b, s in self._named_rows if _collapse(s) == _collapse(street)}
        if not boroughs:
            return ExceptionCheck(provision, EXCEPTION_NOT_APPLICABLE,
                                  f"ZR 12-10 names {named}; {street} is not one of them")
        if _collapse(borough) in _BOROUGH_NAMES and _collapse(borough) not in boroughs:
            return ExceptionCheck(provision, EXCEPTION_NOT_APPLICABLE,
                                  f"ZR 12-10 names {named}; {street} in {borough} is not one "
                                  "of them")
        result = self._matcher.match(OverrideQuery(borough, community_district, street))
        status = (EXCEPTION_NOT_APPLICABLE if result.status == MatchStatus.NOT_MATCHED
                  else EXCEPTION_MAY_APPLY)
        return ExceptionCheck(provision, status, f"{street} ({borough}): {result.reason}",
                              result.provision_id, tuple(result.open_legal_questions))


@lru_cache(maxsize=1)
def _packaged() -> Zr1210Exceptions:
    return Zr1210Exceptions.from_store()  # a raise is not cached, so a later call retries


def default_exceptions() -> Zr1210Exceptions:
    """The packaged snapshot's checks, loaded once (deterministic, no network)."""
    try:
        return _packaged()
    except Exception as exc:  # noqa: BLE001 - fail-safe boundary: any load fault = unchecked
        return Zr1210Exceptions.unavailable(exc)
