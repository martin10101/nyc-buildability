"""Attach each source's version status to the site facts it covers.

Queue item B-06 follow-up; request ``docs/lanes/requests/B-1.md``; site_fact contract
1.1.0. B-06 pins every source behind a site fact and runs the "Out of date" rule
(:mod:`app.profile.data_versions`). B-1 (merged by Lane C) added an OPTIONAL
``source.version_check`` to ``packages/contracts/schemas/v1/site_fact.schema.json``
(contract 1.1.0) so the status can travel with the fact to Lane D (details), Lane E
(report appendix) and ``export_record.sources``.

This module is the bridge. Given the B-02 site facts and the
:class:`~app.profile.data_versions.DataVersionReport` the assessor returned for them,
:func:`attach_version_check` returns NEW fact dicts: each fact whose source the report
assessed carries ``source.version_check`` (the six-key projection of
:meth:`~app.profile.data_versions.SourceVersionStatus.to_dict`) and is stamped contract
1.1.0; every other fact is returned byte-identical and stays 1.0.0 with no key.

Fail closed: the contract co-requires a non-null ``source.dataset_version`` and
``version_check.latest_known_version`` for a ``current`` or ``out_of_date`` status
(``site_fact.schema.json`` ``$defs/source`` allOf and ``$defs/version_check`` allOf). The
B-06 rule only reaches those statuses with a readable pinned and published version, so it
never violates the co-requirement; but if a report ever did, this module leaves the fact
byte-identical rather than emit an invalid fact. It never changes or invents a status: a
``version_unknown`` is attached only when the assessor already said so.

Pure and deterministic: no I/O, no clock, inputs are never changed.
"""

from __future__ import annotations

import copy
from collections.abc import Iterable, Mapping
from typing import Any

from app.profile.data_versions import (
    STATUS_CURRENT,
    STATUS_OUT_OF_DATE,
    DataVersionReport,
    SourceVersionStatus,
)

__all__ = [
    "SITE_FACT_CONTRACT_VERSION_WITH_VERSION_CHECK",
    "VERSION_CHECK_KEYS",
    "attach_version_check",
    "version_check_projection",
]

# The site_fact contract version a fact reaches once a version_check is attached
# (site_fact.schema.json contract_version enum; request docs/lanes/requests/B-1.md).
SITE_FACT_CONTRACT_VERSION_WITH_VERSION_CHECK = "1.1.0"

# The six keys the contract's $defs/version_check allows: the restricted projection of
# SourceVersionStatus.to_dict() (request docs/lanes/requests/B-1.md). to_dict() also
# carries dataset, pinned_version, version_basis, retrieved_at, query_ref, fact_ids and
# exception_label, which the site fact's own source and the results contract already hold,
# so they are dropped here.
VERSION_CHECK_KEYS = (
    "status",
    "label",
    "latest_known_version",
    "latest_known_seen_at",
    "latest_known_query_ref",
    "reason",
)

# Statuses whose version_check co-requires a non-null dataset_version and
# latest_known_version. The rule fails closed to version_unknown, so only these two can
# ever carry the co-requirement.
_VERSIONED_STATUSES = frozenset({STATUS_CURRENT, STATUS_OUT_OF_DATE})


def version_check_projection(status: SourceVersionStatus) -> dict:
    """The six contract keys of ``status`` (``SourceVersionStatus.to_dict()`` restricted)."""
    full = status.to_dict()
    return {key: full[key] for key in VERSION_CHECK_KEYS}


def _non_empty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def attach_version_check(
    facts: Iterable[Mapping[str, Any]],
    report: DataVersionReport,
) -> tuple[dict, ...]:
    """New site_fact dicts carrying ``source.version_check`` for every assessed source.

    Args:
        facts: B-02 ``site_fact`` v1 documents (``app.profile.site_facts.build_site_facts``
            facts). Read, never changed.
        report: the :class:`DataVersionReport` the assessor returned for those facts
            (``app.profile.data_versions.assess_data_versions``). Its sources carry the
            ``fact_ids`` they cover, which is how a status is matched to a fact.

    Returns:
        One new dict per input fact, in input order. A fact whose ``fact_id`` a report
        source covers is a copy with ``source.version_check`` set to that source's six-key
        projection and ``contract_version`` set to "1.1.0". A fact the report did not
        assess (no dataset to pin, or no ``fact_id``) is a byte-identical copy that stays
        1.0.0 with no key. A fact whose ``current``/``out_of_date`` status would violate the
        contract's non-null co-requirement is left byte-identical (fail closed); the status
        is never changed or invented.
    """
    by_fact_id: dict[str, SourceVersionStatus] = {}
    for source in report.sources:
        for fact_id in source.fact_ids:
            by_fact_id[fact_id] = source
    return tuple(_attach_one(fact, by_fact_id) for fact in facts)


def _attach_one(
    fact: Mapping[str, Any], by_fact_id: Mapping[str, SourceVersionStatus]
) -> dict:
    new_fact = copy.deepcopy(dict(fact))
    status = by_fact_id.get(new_fact.get("fact_id"))
    source = new_fact.get("source")
    # Not assessed, or no source object to carry the key: byte-identical, stays 1.0.0.
    if status is None or not isinstance(source, dict):
        return new_fact
    # Fail closed: a versioned status with a null dataset_version or latest_known_version
    # would be an invalid fact (the contract's co-requirement). Leave it byte-identical;
    # never invent or downgrade a status.
    if status.status in _VERSIONED_STATUSES and not (
        _non_empty(source.get("dataset_version"))
        and _non_empty(status.latest_known_version)
    ):
        return new_fact
    source["version_check"] = version_check_projection(status)
    new_fact["contract_version"] = SITE_FACT_CONTRACT_VERSION_WITH_VERSION_CHECK
    return new_fact
