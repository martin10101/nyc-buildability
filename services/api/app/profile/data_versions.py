"""Pinned data versions and the "Out of date" rule (queue item B-06; check C-7, data side).

Check C-7 (``docs/COMPETITOR_REVIEW_ENVELOPE_215-16_NORTHERN_2026-09-28.md`` section D):
"Current sources | Data versions shown and current; every ZR citation exists in the current
Resolution". This module is the data half: "Data versions shown and current". The ZR
citation half belongs to Lane A.

What it does:

- **Pin.** Every source a site fact uses is pinned with its version and retrieval time. The
  version is the one the connector already recorded: the PLUTO or MapPLUTO release (such as
  ``26v2``), or a dataset timestamp (for example the DCM layer's ``dataLastEditDate``, or
  ZTLDB ``rowsUpdatedAt``). The pin is read from the site_fact ``source`` object (``dataset``,
  ``dataset_version``, ``retrieved_at``, ``query_ref``) or from a connector provenance record.
  Nothing is re-fetched.
- **Rule.** A pinned source is compared with the published versions on record for the same
  dataset:

  1. No readable pinned version -> ``version_unknown`` ("Version unknown").
  2. A readable published version newer than the pin -> ``out_of_date`` ("Out of date"),
     with the reason naming both versions and where the newer one was seen.
  3. No readable published version of the same kind, or one that cannot be read or
     compared -> ``version_unknown``.
  4. Otherwise -> ``current``.

  The rule fails closed: an unknown or unreadable version, or a pin nothing can be compared
  with, is never ``current``.

- **No age threshold.** The plan text gives no threshold (the product plan, the lane plan and
  check C-7 say only "shown and current"). So "behind" means only "a newer published version
  is known". The ZTLDB connector's 45-day ``source_stale_suspected`` signal comes from a
  research registry draft, not the plan, so it is not used here.

Version kinds (only the same kind is compared):

- ``release``: ``YYvN`` or ``YYvN.M``. The PLUTO README (research
  ``docs/research/pluto-mappluto-2026-07-16.md`` section 3.2) gives majors (``24v1``) quarterly
  and minors (``24v1.1``) monthly. MapPLUTO uses the same release label. A missing minor
  counts as 0.
- ``timestamp``: an RFC 3339 date-time with a time zone (the site_fact ``date_time`` shape).
  Timestamps are compared as instants, so offsets are honoured. The ZTLDB connector records
  ``rowsUpdatedAt`` as ``socrata-rows-<RFC 3339>`` (``app.connectors.ztldb_soda``
  ``version_label``), and that label reads as its timestamp.

Digits are ASCII ``0-9`` only. When several published versions tie (``26v1`` and ``26v1.0``, or
one instant at two offsets), the latest-seen one is reported, then the one whose version text
sorts last. So the report never depends on input order.

Published versions come from any recorded observation of what a dataset published: a version
probe (for example the PLUTO ``$select=version`` query, fixture F09), layer metadata, or a
retrieval itself (:func:`published_from_pins`: a retrieval shows what was published at that
time).

Output: :class:`DataVersionReport`. Per source: the pinned version, retrieval time, status,
label and reason. For the results contract: ``out_of_date`` and ``out_of_date_reason``, and a
per-fact ``"Out of date"`` exception label (``results.schema.json`` ``exception_label``).
:meth:`DataVersionReport.c7_data_side` is the C-7 data check. The site_fact contract has no
field for the status yet, so it is not attached to the facts (request
``docs/lanes/requests/B-1.md``).

Pure and deterministic: no I/O, no clock, and inputs are never changed.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any

__all__ = [
    "BASIS_RELEASE",
    "BASIS_TIMESTAMP",
    "LABELS",
    "OUT_OF_DATE_EXCEPTION_LABEL",
    "STATUS_CURRENT",
    "STATUS_OUT_OF_DATE",
    "STATUS_VERSION_UNKNOWN",
    "C7DataSide",
    "DataVersionReport",
    "PinnedSource",
    "PublishedVersion",
    "SourceVersionStatus",
    "assess_data_versions",
    "assess_source",
    "pin_from_record",
    "pin_from_site_fact_source",
    "pins_from_site_facts",
    "published_from_pins",
    "read_version",
]

STATUS_CURRENT = "current"
STATUS_OUT_OF_DATE = "out_of_date"
STATUS_VERSION_UNKNOWN = "version_unknown"
LABELS: Mapping[str, str] = {
    STATUS_CURRENT: "Current",
    STATUS_OUT_OF_DATE: "Out of date",
    STATUS_VERSION_UNKNOWN: "Version unknown",
}
# The results contract's exception label beside a number (plan section 5a item 3).
OUT_OF_DATE_EXCEPTION_LABEL = "Out of date"

BASIS_RELEASE = "release"
BASIS_TIMESTAMP = "timestamp"

# PLUTO release format (connector pluto_soda; fixture F09 note), ASCII digits only.
_RELEASE_RE = re.compile(r"^([0-9]{2})v([0-9]+)(?:\.([0-9]+))?$")
# common.schema.json date_time pattern: a time zone is required.
_TIMESTAMP_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$"
)
# ZTLDB dataset_version label: f"socrata-rows-{rows_updated_at}" (ztldb_soda version_label).
_ZTLDB_ROWS_PREFIX = "socrata-rows-"


def _text(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _timestamp(text: str) -> tuple[str, Any] | None:
    if not _TIMESTAMP_RE.match(text):
        return None
    try:
        return BASIS_TIMESTAMP, datetime.fromisoformat(text)
    except ValueError:
        return None


def read_version(version: Any) -> tuple[str, Any] | None:
    """``(kind, sort_key)`` for a readable version, or None (unknown or unreadable)."""
    text = _text(version)
    if text is None:
        return None
    if text.startswith(_ZTLDB_ROWS_PREFIX):
        return _timestamp(text[len(_ZTLDB_ROWS_PREFIX):])
    match = _RELEASE_RE.match(text)
    if match:
        year, major, minor = match.groups()
        return BASIS_RELEASE, (int(year), int(major), int(minor or 0))
    return _timestamp(text)


@dataclass(frozen=True)
class PinnedSource:
    """One source as a site fact used it: dataset, pinned version (None when the source
    recorded none), retrieval time, request, and the fact ids that use it."""

    dataset: str
    version: str | None
    retrieved_at: str | None
    query_ref: str | None
    fact_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class PublishedVersion:
    """A recorded observation that ``dataset`` published ``version``, seen at ``seen_at``
    through ``query_ref``."""

    dataset: str
    version: str | None
    seen_at: str | None
    query_ref: str | None


@dataclass(frozen=True)
class SourceVersionStatus:
    dataset: str
    pinned_version: str | None
    version_basis: str | None
    retrieved_at: str | None
    query_ref: str | None
    fact_ids: tuple[str, ...]
    status: str
    latest_known_version: str | None
    latest_known_seen_at: str | None
    latest_known_query_ref: str | None
    reason: str

    @property
    def label(self) -> str:
        return LABELS[self.status]

    @property
    def exception_label(self) -> str | None:
        """The results ``exception_label`` for numbers from this source."""
        return OUT_OF_DATE_EXCEPTION_LABEL if self.status == STATUS_OUT_OF_DATE else None

    def to_dict(self) -> dict:
        return {
            "dataset": self.dataset,
            "pinned_version": self.pinned_version,
            "version_basis": self.version_basis,
            "retrieved_at": self.retrieved_at,
            "query_ref": self.query_ref,
            "fact_ids": list(self.fact_ids),
            "status": self.status,
            "label": self.label,
            "exception_label": self.exception_label,
            "latest_known_version": self.latest_known_version,
            "latest_known_seen_at": self.latest_known_seen_at,
            "latest_known_query_ref": self.latest_known_query_ref,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class C7DataSide:
    """C-7 data side: passes only when there is at least one source and every one is
    ``current``. ``failures`` holds the reason for each source that is not."""

    passes: bool
    failures: tuple[str, ...]


@dataclass(frozen=True)
class DataVersionReport:
    sources: tuple[SourceVersionStatus, ...]

    def of_status(self, status: str) -> tuple[SourceVersionStatus, ...]:
        return tuple(source for source in self.sources if source.status == status)

    @property
    def out_of_date(self) -> bool:
        return bool(self.of_status(STATUS_OUT_OF_DATE))

    @property
    def out_of_date_reason(self) -> str | None:
        """Text for ``results.out_of_date_reason``; None when no source is behind."""
        reasons = [source.reason for source in self.of_status(STATUS_OUT_OF_DATE)]
        return " ".join(reasons) if reasons else None

    def fact_exception_labels(self) -> dict[str, str]:
        """``fact_id`` -> "Out of date" for each fact whose source is behind."""
        return {
            fact_id: OUT_OF_DATE_EXCEPTION_LABEL
            for source in self.of_status(STATUS_OUT_OF_DATE)
            for fact_id in source.fact_ids
        }

    def c7_data_side(self) -> C7DataSide:
        failures = tuple(
            f"{source.label}: {source.reason}"
            for source in self.sources if source.status != STATUS_CURRENT
        )
        if not self.sources:
            failures = ("No data source is pinned, so no version can be shown.",)
        return C7DataSide(not failures, failures)

    def to_dict(self) -> dict:
        return {
            "sources": [source.to_dict() for source in self.sources],
            "out_of_date": self.out_of_date,
            "out_of_date_reason": self.out_of_date_reason,
        }


def pin_from_site_fact_source(source: Any, fact_ids: Sequence[str] = ()) -> PinnedSource | None:
    """The pin for a site_fact ``source`` object; None when the source is null or names no
    dataset (an architect entry, survey or assumption has no dataset version to check)."""
    if not isinstance(source, Mapping) or _text(source.get("dataset")) is None:
        return None
    return PinnedSource(
        dataset=source["dataset"],
        version=_text(source.get("dataset_version")),
        retrieved_at=_text(source.get("retrieved_at")),
        query_ref=_text(source.get("query_ref")),
        fact_ids=tuple(fact_ids),
    )


def pins_from_site_facts(facts: Iterable[Mapping[str, Any]]) -> tuple[PinnedSource, ...]:
    """One pin per distinct source (dataset, version, retrieval time, request) across the
    site_fact records, with the ids of the facts that use it, in first-seen order."""
    grouped: dict[tuple, list[str]] = {}
    for fact in facts:
        pin = pin_from_site_fact_source(fact.get("source"))
        if pin is None:
            continue
        key = (pin.dataset, pin.version, pin.retrieved_at, pin.query_ref)
        ids = grouped.setdefault(key, [])
        fact_id = _text(fact.get("fact_id"))
        if fact_id is not None and fact_id not in ids:
            ids.append(fact_id)
    return tuple(PinnedSource(*key, fact_ids=tuple(ids)) for key, ids in grouped.items())


def pin_from_record(record: Mapping[str, Any], *, dataset: str,
                    fact_ids: Sequence[str] = ()) -> PinnedSource:
    """The pin for a connector provenance record (``dataset_version``, ``retrieved_at`` and
    ``request_url`` or ``query_ref``), such as the B-03 ``lot_outline`` provenance."""
    return PinnedSource(
        dataset=dataset,
        version=_text(record.get("dataset_version")),
        retrieved_at=_text(record.get("retrieved_at")),
        query_ref=_text(record.get("request_url")) or _text(record.get("query_ref")),
        fact_ids=tuple(fact_ids),
    )


def published_from_pins(pins: Iterable[PinnedSource]) -> tuple[PublishedVersion, ...]:
    """Each retrieval as an observation of what its dataset published at retrieval time."""
    return tuple(PublishedVersion(pin.dataset, pin.version, pin.retrieved_at, pin.query_ref)
                 for pin in pins)


def _describe(pin: PinnedSource) -> str:
    when = f" (retrieved {pin.retrieved_at})" if pin.retrieved_at else ""
    return f"{pin.dataset} {pin.version}{when}"


def assess_source(pin: PinnedSource, published: Iterable[PublishedVersion]) -> SourceVersionStatus:
    """Apply the rule (module docstring) to one pinned source."""
    same_dataset = [seen for seen in published if seen.dataset == pin.dataset]
    pinned = read_version(pin.version)

    def status(code: str, reason: str, latest: PublishedVersion | None = None):
        return SourceVersionStatus(
            dataset=pin.dataset,
            pinned_version=pin.version,
            version_basis=pinned[0] if pinned else None,
            retrieved_at=pin.retrieved_at,
            query_ref=pin.query_ref,
            fact_ids=pin.fact_ids,
            status=code,
            latest_known_version=latest.version if latest else None,
            latest_known_seen_at=latest.seen_at if latest else None,
            latest_known_query_ref=latest.query_ref if latest else None,
            reason=reason,
        )

    # Fail closed: without a readable pinned version the source is never current.
    if pinned is None:
        what = (f"version {pin.version!r} is not a known release or date"
                if pin.version else "has no recorded version")
        return status(STATUS_VERSION_UNKNOWN,
                      f"{pin.dataset} {what}, so it cannot be shown as current.")

    comparable: list[tuple[Any, str, str, str, PublishedVersion]] = []
    unreadable: list[PublishedVersion] = []
    for seen in same_dataset:
        reading = read_version(seen.version)
        if reading is None or reading[0] != pinned[0]:
            unreadable.append(seen)
        else:
            # Ties on the version value break on when it was seen, then its text, then the
            # request, so the reported latest never depends on input order.
            comparable.append((reading[1], seen.seen_at or "", seen.version.strip(),
                               seen.query_ref or "", seen))
    comparable.sort(key=lambda item: item[:4])
    latest = comparable[-1][-1] if comparable else None

    if latest is not None and comparable[-1][0] > pinned[1]:
        seen_at = f" (seen {latest.seen_at})" if latest.seen_at else ""
        return status(STATUS_OUT_OF_DATE,
                      f"{_describe(pin)} is in use; a newer version, {latest.version}, "
                      f"is published{seen_at}.", latest)

    # Fail closed: nothing comparable on record, or a published version that cannot be read
    # or compared, so a newer version cannot be ruled out.
    if latest is None or unreadable:
        if unreadable:
            versions = ", ".join(sorted(repr(seen.version) for seen in unreadable))
            lead = f"Published version(s) on record ({versions}) cannot be compared with"
        else:
            lead = "No published version is on record to compare with"
        return status(STATUS_VERSION_UNKNOWN,
                      f"{lead} {_describe(pin)}, so it cannot be shown as current.", latest)

    checked = f" (checked {latest.seen_at})" if latest.seen_at else ""
    return status(STATUS_CURRENT,
                  f"{_describe(pin)} is the newest published version on record{checked}.",
                  latest)


def assess_data_versions(pins: Iterable[PinnedSource],
                         published: Iterable[PublishedVersion]) -> DataVersionReport:
    """Assess every pin against the published versions on record. Sources are sorted by
    dataset, version, retrieval time, request and fact ids, so input order never changes
    the report."""
    seen = tuple(published)
    ordered = sorted(pins, key=lambda pin: (pin.dataset, pin.version or "",
                                            pin.retrieved_at or "", pin.query_ref or "",
                                            pin.fact_ids))
    return DataVersionReport(tuple(assess_source(pin, seen) for pin in ordered))
