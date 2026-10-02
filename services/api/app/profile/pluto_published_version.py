"""Adapter: a PLUTO version-probe result -> a :class:`PublishedVersion` record.

This is the one small bridge between the Lane B connector probe
(:class:`app.connectors.pluto_version_probe.PlutoPublishedVersion`) and the
pure data-version rule (:mod:`app.profile.data_versions`). Keeping it here lets
``data_versions`` stay connector-free and I/O-free, and lets the connector stay
unaware of the profile layer.

The dataset name must match the one the PLUTO pins carry
(:data:`app.profile.site_facts.PLUTO_DATASET_NAME`, e.g. ``"PLUTO (64uk-42ks)"``),
because :func:`app.profile.data_versions.assess_source` only compares published
versions whose ``dataset`` equals the pin's ``dataset``. Mapping to that exact
name is the whole reason this adapter exists.

Pure and deterministic: a field re-shape only, no I/O and no clock.
"""

from __future__ import annotations

from app.connectors.pluto_version_probe import PlutoPublishedVersion
from app.profile.data_versions import PublishedVersion
from app.profile.site_facts import PLUTO_DATASET_NAME

__all__ = ["published_version_from_probe"]


def published_version_from_probe(probe: PlutoPublishedVersion) -> PublishedVersion:
    """Turn a probe result into a ``PublishedVersion`` for ``assess_data_versions``.

    The probe carries the dataset id (``64uk-42ks``); the version rule keys on
    the human dataset NAME the pins use, so the name is taken from
    ``PLUTO_DATASET_NAME`` (the single source of truth) rather than rebuilt here.
    """
    return PublishedVersion(
        dataset=PLUTO_DATASET_NAME,
        version=probe.version,
        seen_at=probe.seen_at,
        query_ref=probe.query_ref,
    )
